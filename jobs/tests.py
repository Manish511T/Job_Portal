from django.test import override_settings
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import Company
from jobs.models import Job, Skill


User = get_user_model()

@override_settings(
    PASSWORD_HASHERS=[
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
)
class JobAccessTests(APITestCase):

    def setUp(self):
        # Create users with different roles.
        self.employer1 = User.objects.create_user(
            username="employer1",
            email="employer1@example.com",
            password="TestPass123!",
            role="EMPLOYER",
        )

        self.employer2 = User.objects.create_user(
            username="employer2",
            email="employer2@example.com",
            password="TestPass123!",
            role="EMPLOYER",
        )

        self.candidate = User.objects.create_user(
            username="candidate1",
            email="candidate@example.com",
            password="TestPass123!",
            role="CANDIDATE",
        )

        # Create a company for each employer.
        self.company1 = Company.objects.create(
            owner=self.employer1,
            name="Company One",
            description="First test company",
            location="Delhi",
        )

        self.company2 = Company.objects.create(
            owner=self.employer2,
            name="Company Two",
            description="Second test company",
            location="Noida",
        )

        # Create jobs with different visibility statuses.
        self.open_job = self.create_job(
            self.company1,
            "Open Job",
            Job.Status.OPEN,
        )

        self.draft_job = self.create_job(
            self.company1,
            "Draft Job",
            Job.Status.DRAFT,
        )

        self.other_employer_draft = self.create_job(
            self.company2,
            "Other Employer Draft",
            Job.Status.DRAFT,
        )

        self.other_employer_open = self.create_job(
            self.company2,
            "Other Employer Open",
            Job.Status.OPEN,
        )

        self.jobs_url = reverse("job-list-create")
        self.my_jobs_url = reverse("my-jobs")

    def create_job(self, company, title, job_status):
        return Job.objects.create(
            company=company,
            title=title,
            description="Test job description",
            location="Delhi",
            job_type="FULL_TIME",
            status=job_status,
        )

    def job_url(self, job):
        return reverse("job-detail", kwargs={"pk": job.pk})

    def test_public_list_shows_only_open_jobs(self):
        response = self.client.get(self.jobs_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {item["id"] for item in response.data}

        self.assertIn(self.open_job.id, returned_ids)
        self.assertIn(self.other_employer_open.id, returned_ids)
        self.assertNotIn(self.draft_job.id, returned_ids)
        self.assertNotIn(self.other_employer_draft.id, returned_ids)

    def test_public_user_cannot_view_draft(self):
        response = self.client.get(self.job_url(self.draft_job))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_view_own_draft(self):
        self.client.force_authenticate(user=self.employer1)

        response = self.client.get(self.job_url(self.draft_job))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employer_cannot_view_another_employers_draft(self):
        self.client.force_authenticate(user=self.employer1)

        response = self.client.get(
            self.job_url(self.other_employer_draft)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_employer_cannot_edit_another_employers_open_job(self):
        self.client.force_authenticate(user=self.employer1)

        response = self.client.patch(
            self.job_url(self.other_employer_open),
            {"title": "Unauthorized title change"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.other_employer_open.refresh_from_db()
        self.assertEqual(
            self.other_employer_open.title,
            "Other Employer Open",
        )

    def test_employer_cannot_delete_another_employers_job(self):
        self.client.force_authenticate(user=self.employer1)

        response = self.client.delete(
            self.job_url(self.other_employer_open)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Job.objects.filter(pk=self.other_employer_open.pk).exists()
        )

    def test_candidate_cannot_create_job(self):
        self.client.force_authenticate(user=self.candidate)

        response = self.client.post(
            self.jobs_url,
            {
                "title": "Candidate Job",
                "description": "Should not be created",
                "location": "Delhi",
                "job_type": "FULL_TIME",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_can_create_job_under_own_company(self):
        self.client.force_authenticate(user=self.employer1)

        response = self.client.post(
            self.jobs_url,
            {
                "title": "New Test Job",
                "description": "Created by employer",
                "location": "Delhi",
                "job_type": "FULL_TIME",
                "status": Job.Status.OPEN,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_job = Job.objects.get(pk=response.data["id"])
        self.assertEqual(created_job.company_id, self.company1.id)

    def test_employer_cannot_create_job_without_company(self):
        employer_without_company = User.objects.create_user(
            username="employer3",
            email="employer3@example.com",
            password="TestPass123!",
            role="EMPLOYER",
        )

        self.client.force_authenticate(user=employer_without_company)

        response = self.client.post(
            self.jobs_url,
            {
                "title": "Job Without Company",
                "description": "Test description",
                "location": "Delhi",
                "job_type": "FULL_TIME",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_my_jobs_returns_all_own_statuses_only(self):
        self.client.force_authenticate(user=self.employer1)

        response = self.client.get(self.my_jobs_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {item["id"] for item in response.data}

        self.assertIn(self.open_job.id, returned_ids)
        self.assertIn(self.draft_job.id, returned_ids)
        self.assertNotIn(self.other_employer_open.id, returned_ids)
        self.assertNotIn(self.other_employer_draft.id, returned_ids)

    def test_closed_job_with_expired_deadline_cannot_reopen(self):
        expired_job = self.create_job(
            self.company1,
            "Expired Closed Job",
            Job.Status.CLOSED,
        )

        expired_job.deadline = timezone.localdate() - timedelta(days=1)
        expired_job.save(update_fields=["deadline"])

        self.client.force_authenticate(user=self.employer1)

        response = self.client.patch(
            self.job_url(expired_job),
            {"status": Job.Status.OPEN},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        expired_job.refresh_from_db()
        self.assertEqual(expired_job.status, Job.Status.CLOSED)

        
    def test_anonymous_user_cannot_list_skills(self):
        response = self.client.get(reverse("skill-list"))

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


    def test_candidate_can_list_skills(self):
        self.client.force_authenticate(user=self.candidate)

        response = self.client.get(reverse("skill-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_candidate_cannot_create_skill(self):
        self.client.force_authenticate(user=self.candidate)

        response = self.client.post(
            reverse("skill-list"),
            {"name": "Python"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_admin_can_create_skill(self):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin@123",
        )
        self.client.force_authenticate(user=admin)

        response = self.client.post(
            reverse("skill-list"),
            {"name": "Python"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data,)


    def test_employer_cannot_delete_skill(self):
        skill = Skill.objects.create(name="Python")
        self.client.force_authenticate(user=self.employer1)

        response = self.client.delete(
            reverse("skill-detail", kwargs={"pk": skill.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Skill.objects.filter(pk=skill.pk).exists())


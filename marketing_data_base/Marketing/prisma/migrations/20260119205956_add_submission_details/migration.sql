-- AlterTable
ALTER TABLE "JobDescription" ADD COLUMN     "location" TEXT,
ADD COLUMN     "submissionDetails" TEXT,
ALTER COLUMN "company" DROP NOT NULL,
ALTER COLUMN "jobRole" DROP NOT NULL,
ALTER COLUMN "jobDescription" DROP NOT NULL,
ALTER COLUMN "vendorName" DROP NOT NULL,
ALTER COLUMN "vendorContact" DROP NOT NULL,
ALTER COLUMN "vendorEmail" DROP NOT NULL,
ALTER COLUMN "careerLink" DROP NOT NULL;

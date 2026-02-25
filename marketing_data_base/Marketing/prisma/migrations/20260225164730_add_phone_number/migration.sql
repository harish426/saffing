-- AlterTable
ALTER TABLE "JobDescription" ADD COLUMN     "progress" TEXT NOT NULL DEFAULT 'None';

-- AlterTable
ALTER TABLE "Resume" ADD COLUMN     "resumeData" JSONB;

-- AlterTable
ALTER TABLE "User" ADD COLUMN     "phoneNumber" TEXT;

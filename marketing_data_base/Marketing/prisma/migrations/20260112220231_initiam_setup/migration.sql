-- CreateTable
CREATE TABLE "JobDescription" (
    "id" TEXT NOT NULL,
    "company" TEXT NOT NULL,
    "jobRole" TEXT NOT NULL,
    "jobDescription" TEXT NOT NULL,
    "vendorName" TEXT NOT NULL,
    "vendorContact" TEXT NOT NULL,
    "vendorEmail" TEXT NOT NULL,
    "careerLink" TEXT NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "JobDescription_pkey" PRIMARY KEY ("id")
);

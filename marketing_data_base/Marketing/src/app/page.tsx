
import { redirect } from 'next/navigation';
import { verifySession } from '@/lib/auth';
import MultiStepForm from '../components/auth/MultiStepForm';

export default async function Home() {
  // If user is already fully logged in and arrives at '/', send to dashboard.
  // This replaces the middleware redirect which was removed to fix the multi-step
  // signup flow (the middleware was closing the Server Action channel prematurely).
  const user = await verifySession();
  if (user) {
    redirect('/dashboard');
  }

  return (
    <main className="container">
      <div style={{ width: '100%', maxWidth: '1200px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h1 className="heading" style={{ marginBottom: '1rem' }}>Staffing Portal</h1>
        <p style={{ color: '#a1a1aa', marginBottom: '3rem', fontSize: '1.1rem' }}>please complete the onboarding process to continue</p>
        <MultiStepForm />
      </div>
    </main>
  );
}


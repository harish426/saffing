
import MultiStepForm from '../../components/auth/MultiStepForm';
import LogoutButton from '../../components/auth/LogoutButton';

export default function OnboardingPage() {
    return (
        <main className="container" style={{ position: 'relative' }}>
            <LogoutButton />
            <div style={{ padding: '2rem 0' }}>
                <MultiStepForm />
            </div>
        </main>
    );
}

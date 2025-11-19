import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/lib/api/auth';
import { useAuthStore } from './useAuthStore';
import { toast } from 'sonner';
import { LoginInput, RegisterInput } from '@/lib/validators';

export function useAuth() {
    const router = useRouter();
    const { login: setAuth, logout: clearAuth, isAuthenticated, user } = useAuthStore();

    const loginMutation = useMutation({
        mutationFn: authApi.login,
        onSuccess: (data) => {
            setAuth(data.user, data.token);
            toast.success('Welcome back!');
            router.push('/dashboard');
        },
        onError: (error: Error) => {
            toast.error(error.message || 'Failed to login');
        },
    });

    const registerMutation = useMutation({
        mutationFn: authApi.register,
        onSuccess: (data) => {
            setAuth(data.user, data.token);
            toast.success('Account created successfully!');
            router.push('/onboarding'); // Redirect to onboarding after register
        },
        onError: (error: Error) => {
            toast.error(error.message || 'Failed to create account');
        },
    });

    const logoutMutation = useMutation({
        mutationFn: authApi.logout,
        onSuccess: () => {
            clearAuth();
            router.push('/login');
            toast.success('Logged out successfully');
        },
    });

    return {
        user,
        isAuthenticated,
        login: loginMutation.mutate,
        register: registerMutation.mutate,
        logout: logoutMutation.mutate,
        isLoggingIn: loginMutation.isPending,
        isRegistering: registerMutation.isPending,
        isLoggingOut: logoutMutation.isPending,
    };
}

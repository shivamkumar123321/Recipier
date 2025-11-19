import { LoginInput, RegisterInput } from "@/lib/validators";

// Mock API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export interface User {
    id: string;
    name: string;
    email: string;
    avatar?: string;
}

export interface AuthResponse {
    user: User;
    token: string;
}

export const authApi = {
    login: async (credentials: LoginInput): Promise<AuthResponse> => {
        await delay(1000); // Simulate network request

        // Mock successful login
        if (credentials.email === "test@example.com" && credentials.password === "password") {
            return {
                user: {
                    id: "1",
                    name: "Test User",
                    email: credentials.email,
                    avatar: "https://github.com/shadcn.png",
                },
                token: "mock-jwt-token",
            };
        }

        throw new Error("Invalid credentials");
    },

    register: async (data: RegisterInput): Promise<AuthResponse> => {
        await delay(1500);

        return {
            user: {
                id: "2",
                name: data.name,
                email: data.email,
            },
            token: "mock-jwt-token-new",
        };
    },

    logout: async (): Promise<void> => {
        await delay(500);
        // Clear local storage or cookies here
    },

    refreshToken: async (): Promise<string> => {
        await delay(500);
        return "new-mock-jwt-token";
    },
};

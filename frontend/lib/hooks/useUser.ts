/**
 * User Hooks
 *
 * React Query hooks for user operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getCurrentUser,
  updateProfile,
  uploadAvatar,
  deleteAvatar,
  getUserProfile,
  updateDietaryPreferences,
  updateGoals,
  getNotificationSettings,
  updateNotificationSettings,
  changePassword,
  deleteAccount,
  UpdateProfileRequest,
  UpdateDietaryPreferencesRequest,
  UpdateGoalsRequest,
  UpdateNotificationSettingsRequest,
  ChangePasswordRequest,
  DeleteAccountRequest,
} from '../api/user';

/**
 * Query keys for user data
 */
export const userKeys = {
  all: ['user'] as const,
  current: () => [...userKeys.all, 'current'] as const,
  profile: () => [...userKeys.all, 'profile'] as const,
  notifications: () => [...userKeys.all, 'notifications'] as const,
};

/**
 * Get current user
 */
export function useCurrentUser() {
  return useQuery({
    queryKey: userKeys.current(),
    queryFn: getCurrentUser,
  });
}

/**
 * Get user profile
 */
export function useUserProfile() {
  return useQuery({
    queryKey: userKeys.profile(),
    queryFn: getUserProfile,
  });
}

/**
 * Update user profile
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProfileRequest) => updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.current() });
      queryClient.invalidateQueries({ queryKey: userKeys.profile() });
    },
  });
}

/**
 * Upload avatar
 */
export function useUploadAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadAvatar(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.current() });
    },
  });
}

/**
 * Delete avatar
 */
export function useDeleteAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteAvatar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.current() });
    },
  });
}

/**
 * Update dietary preferences
 */
export function useUpdateDietaryPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateDietaryPreferencesRequest) =>
      updateDietaryPreferences(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.profile() });
    },
  });
}

/**
 * Update health goals
 */
export function useUpdateGoals() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateGoalsRequest) => updateGoals(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.profile() });
    },
  });
}

/**
 * Get notification settings
 */
export function useNotificationSettings() {
  return useQuery({
    queryKey: userKeys.notifications(),
    queryFn: getNotificationSettings,
  });
}

/**
 * Update notification settings
 */
export function useUpdateNotificationSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateNotificationSettingsRequest) =>
      updateNotificationSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.notifications() });
    },
  });
}

/**
 * Change password
 */
export function useChangePassword() {
  return useMutation({
    mutationFn: (data: ChangePasswordRequest) => changePassword(data),
  });
}

/**
 * Delete account
 */
export function useDeleteAccount() {
  return useMutation({
    mutationFn: (data: DeleteAccountRequest) => deleteAccount(data),
  });
}

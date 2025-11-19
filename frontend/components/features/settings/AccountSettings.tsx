/**
 * AccountSettings Component
 *
 * Manage account security and danger zone actions
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Lock, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useChangePassword, useDeleteAccount } from '@/lib/hooks/useUser';

export function AccountSettings() {
  const router = useRouter();
  const changePasswordMutation = useChangePassword();
  const deleteAccountMutation = useDeleteAccount();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [deletePassword, setDeletePassword] = useState('');
  const [deleteConfirmation, setDeleteConfirmation] = useState('');

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      alert('New passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      alert('Password must be at least 8 characters long');
      return;
    }

    try {
      await changePasswordMutation.mutateAsync({
        current_password: currentPassword,
        new_password: newPassword,
      });

      alert('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      console.error('Failed to change password:', error);
      alert(error.response?.data?.detail || 'Failed to change password. Please try again.');
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmation !== 'DELETE') {
      alert('Please type DELETE to confirm account deletion');
      return;
    }

    try {
      await deleteAccountMutation.mutateAsync({
        password: deletePassword,
        confirmation: deleteConfirmation,
      });

      alert('Your account has been deleted. Redirecting...');
      router.push('/');
    } catch (error: any) {
      console.error('Failed to delete account:', error);
      alert(error.response?.data?.detail || 'Failed to delete account. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Change Password */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="h-5 w-5" />
            Change Password
          </CardTitle>
          <CardDescription>
            Update your password to keep your account secure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="current-password">Current Password</Label>
              <Input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-password">New Password</Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
              />
              <p className="text-xs text-muted-foreground">
                Must be at least 8 characters
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <Input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>

            <Button
              type="submit"
              disabled={changePasswordMutation.isPending}
            >
              {changePasswordMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Changing Password...
                </>
              ) : (
                'Change Password'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Danger Zone
          </CardTitle>
          <CardDescription>
            Irreversible and destructive actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4">
            <h4 className="font-semibold">Delete Account</h4>
            <p className="mt-1 text-sm text-muted-foreground">
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>

            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" className="mt-4">
                  Delete My Account
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone. This will permanently delete your
                    account and remove all your data from our servers.
                  </AlertDialogDescription>
                </AlertDialogHeader>

                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="delete-password">Enter your password</Label>
                    <Input
                      id="delete-password"
                      type="password"
                      value={deletePassword}
                      onChange={(e) => setDeletePassword(e.target.value)}
                      placeholder="Your password"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="delete-confirmation">
                      Type <strong>DELETE</strong> to confirm
                    </Label>
                    <Input
                      id="delete-confirmation"
                      value={deleteConfirmation}
                      onChange={(e) => setDeleteConfirmation(e.target.value)}
                      placeholder="DELETE"
                    />
                  </div>
                </div>

                <AlertDialogFooter>
                  <AlertDialogCancel onClick={() => {
                    setDeletePassword('');
                    setDeleteConfirmation('');
                  }}>
                    Cancel
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleDeleteAccount}
                    disabled={
                      deleteAccountMutation.isPending ||
                      deleteConfirmation !== 'DELETE'
                    }
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    {deleteAccountMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Deleting...
                      </>
                    ) : (
                      'Delete Account'
                    )}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

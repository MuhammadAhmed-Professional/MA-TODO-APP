import { redirect } from 'next/navigation';

/**
 * Chat Page - Redirects to localized version
 */
export default function ChatPage() {
  redirect('/en/chat');
}

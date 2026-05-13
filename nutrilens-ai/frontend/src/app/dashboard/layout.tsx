import DashboardLayout from '@/components/layout/DashboardLayout';
import '../dashboard-dark.css';

export default function Layout({ children }: { children: React.ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>;
}

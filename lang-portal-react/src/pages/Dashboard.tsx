
import { Card } from "@/components/ui/card";

const DashboardCard = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <Card className="p-6 hover:shadow-lg transition-shadow duration-200">
    <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
    {children}
  </Card>
);

const Dashboard = () => {
  return (
    <div className="animate-fadeIn">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome Back</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard title="Recent Activity">
          <p className="text-gray-600">No recent activity</p>
        </DashboardCard>
        <DashboardCard title="Study Progress">
          <p className="text-gray-600">Start studying to see your progress</p>
        </DashboardCard>
        <DashboardCard title="Word Count">
          <p className="text-gray-600">0 words learned</p>
        </DashboardCard>
      </div>
    </div>
  );
};

export default Dashboard;

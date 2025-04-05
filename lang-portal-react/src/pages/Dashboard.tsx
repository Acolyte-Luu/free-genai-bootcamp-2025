import { Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from 'date-fns';

import { 
  fetchLastStudySession, 
  fetchStudyProgress, 
} from "@/lib/api";

const DashboardCard = ({ title, children, isLoading = false, isError = false, errorMsg = "Error loading data" }: { 
  title: string; 
  children: React.ReactNode; 
  isLoading?: boolean;
  isError?: boolean;
  errorMsg?: string;
}) => (
  <Card className="p-6 hover:shadow-lg transition-shadow duration-200 min-h-[120px]">
    <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
    {isLoading && <p className="text-gray-500">Loading...</p>}
    {isError && <p className="text-red-500">{errorMsg}</p>}
    {!isLoading && !isError && children}
  </Card>
);

const Dashboard = () => {

  const { 
    data: lastSessionResponse, 
    isLoading: isLoadingSession, 
    isError: isErrorSession, 
    error: errorSession 
  } = useQuery({
    queryKey: ['lastStudySession'],
    queryFn: fetchLastStudySession,
  });

  const { 
    data: progressResponse, 
    isLoading: isLoadingProgress, 
    isError: isErrorProgress, 
    error: errorProgress 
  } = useQuery({
    queryKey: ['studyProgress'],
    queryFn: fetchStudyProgress,
  });

  const lastSession = lastSessionResponse?.data;
  const progress = progressResponse?.data;

  return (
    <div className="animate-fadeIn">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome Back</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard 
          title="Recent Activity"
          isLoading={isLoadingSession}
          isError={isErrorSession}
          errorMsg={errorSession instanceof Error ? errorSession.message : "Error loading session"}
        >
          {lastSession ? (
            <div className="text-gray-600 space-y-1">
              <p>
                Studied <Link to={`/groups/${lastSession.group_id}`} className="font-medium text-japanese-600 hover:underline">{lastSession.group_name}</Link>
              </p>
              <p>Scored {lastSession.correct_count} / {lastSession.total_words}</p>
              <p className="text-sm text-gray-500">
                {formatDistanceToNow(new Date(lastSession.created_at), { addSuffix: true })}
              </p>
            </div>
          ) : (
            <p className="text-gray-600">No recent activity</p>
          )}
        </DashboardCard>

        <DashboardCard 
          title="Study Progress"
          isLoading={isLoadingProgress}
          isError={isErrorProgress}
          errorMsg={errorProgress instanceof Error ? errorProgress.message : "Error loading progress"}
        >
          {progress ? (
            <p className="text-gray-600">
              Studied {progress.total_words_studied} out of {progress.total_words} words.
            </p>
          ) : (
            <p className="text-gray-600">Start studying to see your progress</p>
          )}
        </DashboardCard>

        <DashboardCard 
          title="Words Studied"
          isLoading={isLoadingProgress}
          isError={isErrorProgress}
          errorMsg={errorProgress instanceof Error ? errorProgress.message : "Error loading progress"}
        >
           {progress ? (
            <p className="text-gray-600">{progress.total_words_studied} words</p>
          ) : (
            <p className="text-gray-600">0 words learned</p>
          )}
        </DashboardCard>
      </div>
    </div>
  );
};

export default Dashboard;

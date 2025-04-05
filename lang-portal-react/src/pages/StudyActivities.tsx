import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type StudyActivity = {
  id: number;
  title: string;
  description: string;
  thumbnail: string;
};

const StudyActivities = () => {
  // Temporary mock data - replace with real data later
  const mockActivities: StudyActivity[] = [
    {
      id: 1,
      title: "Adventure MUD",
      description: "Learn Japanese through an interactive text adventure",
      thumbnail: "/placeholder.svg",
    },
    {
      id: 2,
      title: "Typing Tutor",
      description: "Practice typing Japanese characters",
      thumbnail: "/placeholder.svg",
    },
    {
      id: 3,
      title: "Flashcards",
      description: "Review vocabulary with flashcards",
      thumbnail: "/placeholder.svg",
    },
  ];

  const handleLaunch = (activityId: number, groupId: number = 3) => {
    // TODO: Replace with the actual URL of your deployed jp-mud frontend
    const jpMudAppUrl = 'http://localhost:5173/'; 
    const defaultUrl = `http://localhost:8080?group_id=${groupId}`; // Keep original or define others

    if (activityId === 1) { // Assuming 1 is the ID for "Adventure MUD"
      // window.open(jpMudAppUrl, '_blank'); // Original: Opens in new tab
      window.location.href = jpMudAppUrl; // Navigate current tab
    } else {
      // Handle other activities if needed, maybe open defaultUrl or specific URLs
      // For now, let's keep the original behavior for other activities
      window.open(defaultUrl, '_blank'); 
      // Or perhaps show an alert:
      // alert(`Activity ${activityId} launch not implemented yet.`);
    }
  };

  return (
    <div className="animate-fadeIn">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Study Activities</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockActivities.map((activity) => (
          <Card key={activity.id} className="overflow-hidden">
            <div className="aspect-video bg-gray-100">
              <img
                src={activity.thumbnail}
                alt={activity.title}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {activity.title}
              </h3>
              <p className="text-gray-600 mb-4">{activity.description}</p>
              <div className="flex gap-3">
                <Button
                  onClick={() => handleLaunch(activity.id)}
                  className="flex-1"
                >
                  Launch
                </Button>
                <Button
                  variant="outline"
                  onClick={() => window.location.href = `/study_activities/${activity.id}`}
                  className="flex-1"
                >
                  View
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default StudyActivities;

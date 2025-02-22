
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
    window.open(`http://localhost:8080?group_id=${groupId}`, '_blank');
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

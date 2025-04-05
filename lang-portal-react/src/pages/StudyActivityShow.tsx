import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Session = {
  id: number;
  groupId: number;
  groupName: string;
  startTime: string;
  endTime: string;
  reviewItems: number;
};

const StudyActivityShow = () => {
  const { id } = useParams();
  
  // Temporary mock data - replace with real data later
  const activity = {
    id: Number(id),
    title: "Adventure MUD",
    description: "Learn Japanese through an interactive text adventure game where you explore virtual environments and interact with characters using Japanese language.",
    thumbnail: "/placeholder.svg",
  };

  const mockSessions: Session[] = [
    {
      id: 1,
      groupId: 1,
      groupName: "Core Verbs",
      startTime: "2024-03-15 14:30",
      endTime: "2024-03-15 14:45",
      reviewItems: 25,
    },
  ];

  const handleLaunch = (groupId: number = 3) => {
    // Activity object is defined earlier in the component using useParams
    const jpMudAppUrl = 'http://localhost:5173/';
    const defaultUrl = `http://localhost:8080?group_id=${groupId}`;

    // Check if the current activity's ID is 1 (assuming this corresponds to Adventure MUD)
    if (activity.id === 1) { 
      window.location.href = jpMudAppUrl; // Navigate current tab to jp-mud app
    } else {
      // Keep original behavior for other activities (opens defaultUrl in new tab)
      window.open(defaultUrl, '_blank'); 
    }
  };

  return (
    <div className="animate-fadeIn space-y-8">
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="aspect-video bg-gray-100">
          <img
            src={activity.thumbnail}
            alt={activity.title}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{activity.title}</h1>
          <p className="text-gray-600 mb-6">{activity.description}</p>
          <Button onClick={() => handleLaunch(3)} size="lg">
            Launch Activity
          </Button>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Sessions</h2>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Group</TableHead>
                <TableHead>Start Time</TableHead>
                <TableHead>End Time</TableHead>
                <TableHead>Review Items</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockSessions.map((session) => (
                <TableRow key={session.id}>
                  <TableCell>
                    <Link
                      to={`/groups/${session.groupId}`}
                      className="text-japanese-600 hover:text-japanese-700"
                    >
                      {session.groupName}
                    </Link>
                  </TableCell>
                  <TableCell>{session.startTime}</TableCell>
                  <TableCell>{session.endTime}</TableCell>
                  <TableCell>{session.reviewItems}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
};

export default StudyActivityShow;

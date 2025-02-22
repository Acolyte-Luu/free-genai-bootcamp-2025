
import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

type Session = {
  id: number;
  groupId: number;
  groupName: string;
  activityName: string;
  startTime: string;
  endTime: string;
  reviewItems: number;
};

type SortField = "groupName" | "activityName" | "startTime" | "endTime" | "reviewItems";
type SortDirection = "asc" | "desc";

const Sessions = () => {
  const [sortField, setSortField] = useState<SortField>("startTime");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [currentPage, setCurrentPage] = useState(1);

  // Temporary mock data - replace with real data later
  const mockSessions: Session[] = [
    {
      id: 1,
      groupId: 1,
      groupName: "Core Verbs",
      activityName: "Flashcards",
      startTime: "2024-03-15 14:30",
      endTime: "2024-03-15 14:45",
      reviewItems: 25,
    },
    {
      id: 2,
      groupId: 2,
      groupName: "Basic Adjectives",
      activityName: "Typing Tutor",
      startTime: "2024-03-15 15:00",
      endTime: "2024-03-15 15:20",
      reviewItems: 30,
    },
  ];

  const totalPages = Math.ceil(mockSessions.length / 50);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const getSortIndicator = (field: SortField) => {
    if (sortField !== field) return null;
    return sortDirection === "asc" ? "↓" : "↑";
  };

  return (
    <div className="animate-fadeIn">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Study Sessions</h1>
      
      <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("groupName")}
              >
                Group {getSortIndicator("groupName")}
              </TableHead>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("activityName")}
              >
                Activity {getSortIndicator("activityName")}
              </TableHead>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("startTime")}
              >
                Start Time {getSortIndicator("startTime")}
              </TableHead>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("endTime")}
              >
                End Time {getSortIndicator("endTime")}
              </TableHead>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("reviewItems")}
              >
                Review Items {getSortIndicator("reviewItems")}
              </TableHead>
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
                <TableCell>{session.activityName}</TableCell>
                <TableCell>{session.startTime}</TableCell>
                <TableCell>{session.endTime}</TableCell>
                <TableCell>{session.reviewItems}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              href="#"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              className={currentPage === 1 ? "pointer-events-none opacity-50" : ""}
            />
          </PaginationItem>
          <PaginationItem>
            <PaginationLink>
              Page <span className="font-bold">{currentPage}</span> of {totalPages}
            </PaginationLink>
          </PaginationItem>
          <PaginationItem>
            <PaginationNext
              href="#"
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              className={currentPage === totalPages ? "pointer-events-none opacity-50" : ""}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

export default Sessions;

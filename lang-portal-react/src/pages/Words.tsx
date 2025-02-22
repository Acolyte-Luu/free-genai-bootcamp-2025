
import { useState } from "react";
import { Link } from "react-router-dom";
import { Volume2 } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

type Word = {
  id: number;
  japanese: string;
  romaji: string;
  english: string;
  correct: number;
  wrong: number;
  audioUrl?: string;
};

type SortField = "japanese" | "romaji" | "english" | "correct" | "wrong";
type SortDirection = "asc" | "desc";

const Words = () => {
  const [sortField, setSortField] = useState<SortField>("japanese");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [currentPage, setCurrentPage] = useState(1);

  // Temporary mock data - replace with real data later
  const mockWords: Word[] = [
    {
      id: 1,
      japanese: "水",
      romaji: "mizu",
      english: "water",
      correct: 10,
      wrong: 2,
    },
    // Add more mock data as needed
  ];

  const totalPages = Math.ceil(mockWords.length / 50);

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

  const playAudio = (audioUrl: string) => {
    const audio = new Audio(audioUrl);
    audio.play().catch(console.error);
  };

  return (
    <div className="animate-fadeIn">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Words</h1>
      
      <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("japanese")}
              >
                Japanese {getSortIndicator("japanese")}
              </TableHead>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("romaji")}
              >
                Romaji {getSortIndicator("romaji")}
              </TableHead>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("english")}
              >
                English {getSortIndicator("english")}
              </TableHead>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("correct")}
              >
                Correct {getSortIndicator("correct")}
              </TableHead>
              <TableHead
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort("wrong")}
              >
                Wrong {getSortIndicator("wrong")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {mockWords.map((word) => (
              <TableRow key={word.id}>
                <TableCell className="flex items-center space-x-2">
                  <Link
                    to={`/words/${word.id}`}
                    className="text-japanese-600 hover:text-japanese-700"
                  >
                    {word.japanese}
                  </Link>
                  {word.audioUrl && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => playAudio(word.audioUrl!)}
                      className="p-1"
                    >
                      <Volume2 className="h-4 w-4" />
                    </Button>
                  )}
                </TableCell>
                <TableCell>{word.romaji}</TableCell>
                <TableCell>{word.english}</TableCell>
                <TableCell>{word.correct}</TableCell>
                <TableCell>{word.wrong}</TableCell>
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

export default Words;

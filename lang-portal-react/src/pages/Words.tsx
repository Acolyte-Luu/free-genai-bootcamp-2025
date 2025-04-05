import { useState } from "react";
import { Link } from "react-router-dom";
import { Volume2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
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
import { fetchWords } from "@/lib/api";
import { ApiWord } from "@/types/api";

type SortField = "japanese" | "romaji" | "english" | "correct_count" | "incorrect_count";
type SortDirection = "asc" | "desc";

const Words = () => {
  const [sortField, setSortField] = useState<SortField>("japanese");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  const { data: apiResponse, isLoading, isError, error } = useQuery({
    queryKey: ['words', currentPage],
    queryFn: () => fetchWords(currentPage, itemsPerPage),
    placeholderData: (previousData) => previousData,
  });

  const words = apiResponse?.data ?? [];
  const pagination = apiResponse?.pagination;
  const totalPages = pagination?.total_pages ?? 1;

  const sortedWords = [...words].sort((a, b) => {
    const fieldA = a[sortField];
    const fieldB = b[sortField];
    let comparison = 0;

    if (typeof fieldA === 'string' && typeof fieldB === 'string') {
      comparison = fieldA.localeCompare(fieldB);
    } else if (typeof fieldA === 'number' && typeof fieldB === 'number') {
      comparison = fieldA - fieldB;
    }

    return sortDirection === 'asc' ? comparison : comparison * -1;
  });

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
    console.warn("Audio playback not implemented with backend data yet.");
  };

  return (
    <div className="animate-fadeIn">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Words</h1>
      
      {isLoading && <p>Loading words...</p>}
      {isError && <p>Error loading words: {error instanceof Error ? error.message : 'Unknown error'}</p>}
      
      {!isLoading && !isError && (
        <>
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
                    onClick={() => handleSort("correct_count")}
                  >
                    Correct {getSortIndicator("correct_count")}
                  </TableHead>
                  <TableHead
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => handleSort("incorrect_count")}
                  >
                    Wrong {getSortIndicator("incorrect_count")}
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedWords.map((word: ApiWord) => (
                  <TableRow key={word.id}>
                    <TableCell className="flex items-center space-x-2">
                      <Link
                        to={`/words/${word.id}`}
                        className="text-japanese-600 hover:text-japanese-700"
                      >
                        {word.japanese}
                      </Link>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => playAudio("dummyUrl")}
                        className="p-1 opacity-50"
                        disabled
                        title="Audio playback TBD"
                      >
                        <Volume2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                    <TableCell>{word.romaji}</TableCell>
                    <TableCell>{word.english}</TableCell>
                    <TableCell>{word.correct_count}</TableCell>
                    <TableCell>{word.incorrect_count}</TableCell>
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
        </>
      )}
    </div>
  );
};

export default Words;

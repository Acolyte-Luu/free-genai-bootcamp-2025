import { useParams, Link } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Volume2 } from "lucide-react";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchGroupById, fetchWordsForGroup, fetchSessionsForGroup } from "@/lib/api";
import { SingleGroupData, GroupWord, GroupSession } from "@/types/api";
import { format, formatDistanceStrict } from 'date-fns';

type SortField = "japanese" | "romaji" | "english" | "correct_count" | "incorrect_count";
type SortDirection = "asc" | "desc";

const GroupShow = () => {
  const { id: groupId } = useParams<{ id: string }>();
  const [wordSortField, setWordSortField] = useState<SortField>("japanese");
  const [wordSortDirection, setWordSortDirection] = useState<SortDirection>("asc");
  const [wordCurrentPage, setWordCurrentPage] = useState(1);
  const wordsPerPage = 50;

  const [sessionCurrentPage, setSessionCurrentPage] = useState(1);
  const sessionsPerPage = 10;

  const { 
    data: groupData, 
    isLoading: isLoadingGroup, 
    isError: isErrorGroup, 
    error: errorGroup 
  } = useQuery({
    queryKey: ['group', groupId], 
    queryFn: () => fetchGroupById(groupId!),
    enabled: !!groupId,
  });

  const { 
    data: wordsResponse, 
    isLoading: isLoadingWords, 
    isError: isErrorWords, 
    error: errorWords 
  } = useQuery({
    queryKey: ['groupWords', groupId, wordCurrentPage], 
    queryFn: () => fetchWordsForGroup(groupId!, wordCurrentPage, wordsPerPage),
    enabled: !!groupId,
    placeholderData: (previousData) => previousData, 
  });

  const { 
    data: sessionsResponse, 
    isLoading: isLoadingSessions, 
    isError: isErrorSessions, 
    error: errorSessions 
  } = useQuery({
    queryKey: ['groupSessions', groupId, sessionCurrentPage], 
    queryFn: () => fetchSessionsForGroup(groupId!, sessionCurrentPage, sessionsPerPage),
    enabled: !!groupId,
    placeholderData: (previousData) => previousData,
  });

  const group = groupData?.data;
  const words = Array.isArray(wordsResponse?.data?.data) ? wordsResponse.data.data : [];
  const wordsPagination = wordsResponse?.data?.pagination;
  const wordsTotalPages = wordsPagination?.total_pages ?? 1;
  
  const sessions = sessionsResponse?.data ?? [];
  const sessionsPagination = sessionsResponse?.pagination;
  const sessionsTotalPages = sessionsPagination?.total_pages ?? 1;

  const sortedWords = [...words].sort((a, b) => {
    let comparison = 0;
    if (wordSortField === 'correct_count' || wordSortField === 'incorrect_count') {
      const statA = a.stats?.[wordSortField];
      const statB = b.stats?.[wordSortField];
      comparison = (statA ?? 0) - (statB ?? 0);
    } else {
      const fieldA = a[wordSortField as keyof Omit<GroupWord, 'stats'>];
      const fieldB = b[wordSortField as keyof Omit<GroupWord, 'stats'>];
      if (typeof fieldA === 'string' && typeof fieldB === 'string') {
        comparison = fieldA.localeCompare(fieldB);
      } else if (typeof fieldA === 'number' && typeof fieldB === 'number') {
        comparison = fieldA - fieldB; 
      }
    }
    return wordSortDirection === 'asc' ? comparison : comparison * -1;
  });

  const handleWordSort = (field: SortField) => {
    if (wordSortField === field) {
      setWordSortDirection(wordSortDirection === "asc" ? "desc" : "asc");
    } else {
      setWordSortField(field);
      setWordSortDirection("asc");
    }
  };

  const getWordSortIndicator = (field: SortField) => {
    if (wordSortField !== field) return null;
    return wordSortDirection === "asc" ? "↓" : "↑";
  };

  const playAudio = (/* audioUrl: string */) => {
    console.warn("Audio playback not implemented with backend data yet.");
  };

  if (isLoadingGroup) {
    return <p>Loading group details...</p>;
  }

  if (isErrorGroup) {
    return <p>Error loading group details: {errorGroup instanceof Error ? errorGroup.message : 'Unknown error'}</p>;
  }
  
  if (isErrorWords) {
    return <p>Error loading words for this group: {errorWords instanceof Error ? errorWords.message : 'Unknown error'}</p>;
  }

  if (!group) {
    return <p>Group not found.</p>;
  }

  return (
    <div className="animate-fadeIn space-y-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{group.name}</h1>
        <p className="text-gray-600">Total words: {group.stats?.total_word_count ?? 'N/A'}</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Words in this Group</h2>
        {isLoadingWords && <p>Loading words...</p>}
        {isErrorWords && <p>Error loading words: {errorWords instanceof Error ? errorWords.message : 'Unknown error'}</p>}
        {!isLoadingWords && !isErrorWords && (
          <>
            <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="cursor-pointer" onClick={() => handleWordSort("japanese")}>Japanese {getWordSortIndicator("japanese")}</TableHead>
                    <TableHead className="cursor-pointer" onClick={() => handleWordSort("romaji")}>Romaji {getWordSortIndicator("romaji")}</TableHead>
                    <TableHead className="cursor-pointer" onClick={() => handleWordSort("english")}>English {getWordSortIndicator("english")}</TableHead>
                    <TableHead className="cursor-pointer" onClick={() => handleWordSort("correct_count")}>Correct {getWordSortIndicator("correct_count")}</TableHead>
                    <TableHead className="cursor-pointer" onClick={() => handleWordSort("incorrect_count")}>Wrong {getWordSortIndicator("incorrect_count")}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedWords.length === 0 ? (
                    <TableRow><TableCell colSpan={5} className="h-24 text-center">No words found in this group.</TableCell></TableRow>
                  ) : (
                    sortedWords.map((word: GroupWord, index: number) => (
                      <TableRow key={word.japanese || index}>
                        <TableCell className="flex items-center space-x-2">
                          <span>{word.japanese}</span>
                          <Button variant="ghost" size="sm" onClick={() => playAudio()} className="p-1 opacity-50" disabled title="Audio playback TBD">
                            <Volume2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                        <TableCell>{word.romaji}</TableCell>
                        <TableCell>{word.english}</TableCell>
                        <TableCell>{word.stats?.correct_count ?? 0}</TableCell>
                        <TableCell>{word.stats?.incorrect_count ?? 0}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious href="#" onClick={() => setWordCurrentPage(p => Math.max(1, p - 1))} className={wordCurrentPage === 1 ? "pointer-events-none opacity-50" : ""} />
                </PaginationItem>
                <PaginationItem><PaginationLink>Page {wordCurrentPage} of {wordsTotalPages}</PaginationLink></PaginationItem>
                <PaginationItem>
                  <PaginationNext href="#" onClick={() => setWordCurrentPage(p => Math.min(wordsTotalPages, p + 1))} className={wordCurrentPage === wordsTotalPages ? "pointer-events-none opacity-50" : ""} />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </>
        )}
      </div>
      
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Study Sessions</h2>
        {isLoadingSessions && <p>Loading sessions...</p>}
        {isErrorSessions && <p>Error loading sessions: {errorSessions instanceof Error ? errorSessions.message : 'Unknown error'}</p>}
        {!isLoadingSessions && !isErrorSessions && (
           <>
            <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Activity</TableHead>
                    <TableHead>Reviewed</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Duration</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessions.length === 0 ? (
                     <TableRow><TableCell colSpan={4} className="h-24 text-center">No study sessions recorded for this group yet.</TableCell></TableRow>
                  ) : (
                    sessions.map((session: GroupSession) => (
                      <TableRow key={session.id}>
                        <TableCell>{session.activity_name}</TableCell>
                        <TableCell>{session.review_items_count} words</TableCell>
                        <TableCell>{format(new Date(session.start_time), 'PPp')}</TableCell>
                        <TableCell>
                          {formatDistanceStrict(new Date(session.end_time), new Date(session.start_time))}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious href="#" onClick={() => setSessionCurrentPage(p => Math.max(1, p - 1))} className={sessionCurrentPage === 1 ? "pointer-events-none opacity-50" : ""} />
                </PaginationItem>
                <PaginationItem><PaginationLink>Page {sessionCurrentPage} of {sessionsTotalPages}</PaginationLink></PaginationItem>
                <PaginationItem>
                  <PaginationNext href="#" onClick={() => setSessionCurrentPage(p => Math.min(sessionsTotalPages, p + 1))} className={sessionCurrentPage === sessionsTotalPages ? "pointer-events-none opacity-50" : ""} />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </>
        )}
      </div>
    </div>
  );
};

export default GroupShow;

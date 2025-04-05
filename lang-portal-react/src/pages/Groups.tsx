import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
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
import { fetchGroups } from "@/lib/api";
import { ApiGroup } from "@/types/api";

type SortField = "name";
type SortDirection = "asc" | "desc";

const Groups = () => {
  const [sortField, setSortField] = useState<SortField>("name");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  const { data: apiResponse, isLoading, isError, error } = useQuery({
    queryKey: ['groups', currentPage], 
    queryFn: () => fetchGroups(currentPage, itemsPerPage),
    placeholderData: (previousData) => previousData,
  });

  const groups = apiResponse?.data ?? [];
  const pagination = apiResponse?.pagination;
  const totalPages = pagination?.total_pages ?? 1;

  const sortedGroups = [...groups].sort((a, b) => {
    let comparison = 0;
    if (sortField === 'name') {
        comparison = a.name.localeCompare(b.name);
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

  return (
    <div className="animate-fadeIn">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Word Groups</h1>
      
      {isLoading && <p>Loading groups...</p>}
      {isError && <p>Error loading groups: {error instanceof Error ? error.message : 'Unknown error'}</p>}
      
      {!isLoading && !isError && (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => handleSort("name")}
                  >
                    Group Name {getSortIndicator("name")}
                  </TableHead>
                  {/* Remove Word Count header as it's not in API data */}
                  {/* The TableHead for wordCount below was removed. */}
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedGroups.map((group: ApiGroup) => (
                  <TableRow key={group.id}>
                    <TableCell>
                      <Link
                        to={`/groups/${group.id}`}
                        className="text-japanese-600 hover:text-japanese-700"
                      >
                        {group.name}
                      </Link>
                    </TableCell>
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

export default Groups;

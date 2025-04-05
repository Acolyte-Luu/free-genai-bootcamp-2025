import { useParams, Link } from "react-router-dom";
import { Volume2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { fetchWordById } from "@/lib/api";
import { ApiWord, ApiGroupInfo } from "@/types/api";

const WordShow = () => {
  const { id } = useParams<{ id: string }>();

  const { data: apiResponse, isLoading, isError, error, isSuccess } = useQuery({
    queryKey: ['word', id],
    queryFn: () => fetchWordById(id!),
    enabled: !!id,
  });

  const word = apiResponse?.data;
  const groups = apiResponse?.groups ?? [];

  const playAudio = (/* audioUrl: string */) => {
    console.warn("Audio playback not implemented with backend data yet.");
    // const audio = new Audio(audioUrl);
    // audio.play().catch(console.error);
  };

  return (
    <div className="animate-fadeIn space-y-8">
      {isLoading && <p>Loading word details...</p>}
      {isError && <p>Error loading word: {error instanceof Error ? error.message : 'Unknown error'}</p>}

      {isSuccess && word && (
        <>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-4 mb-6">
              <h1 className="text-4xl font-bold text-gray-900">{word.japanese}</h1>
              <Button
                variant="outline"
                size="icon"
                onClick={() => playAudio(/* "dummyUrl" */)}
                disabled
                title="Audio playback TBD"
              >
                <Volume2 className="h-6 w-6" />
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Reading</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg">{word.romaji}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Meaning</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg">{word.english}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Part of Speech</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg">{word.parts}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between text-lg">
                    <span>Correct: <span className="text-green-600">{word.correct_count}</span></span>
                    <span>Wrong: <span className="text-red-600">{word.incorrect_count}</span></span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Groups</h2>
            {groups.length > 0 ? (
              <div className="bg-white rounded-lg shadow p-4 space-y-2">
                {groups.map((group: ApiGroupInfo) => (
                  <Link 
                    key={group.id} 
                    to={`/groups/${group.id}`}
                    className="block p-2 hover:bg-gray-100 rounded"
                  >
                    {group.name}
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">This word is not part of any group yet.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default WordShow;

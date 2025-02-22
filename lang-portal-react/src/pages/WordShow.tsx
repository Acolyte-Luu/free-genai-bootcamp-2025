
import { useParams } from "react-router-dom";
import { Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const WordShow = () => {
  const { id } = useParams();

  // Temporary mock data - replace with real data later
  const word = {
    id: Number(id),
    japanese: "水",
    romaji: "mizu",
    english: "water",
    correct: 10,
    wrong: 2,
    audioUrl: "/audio/mizu.mp3",
    examples: [
      {
        japanese: "水を飲みます",
        romaji: "mizu wo nomimasu",
        english: "I drink water",
      },
    ],
  };

  const playAudio = (audioUrl: string) => {
    const audio = new Audio(audioUrl);
    audio.play().catch(console.error);
  };

  return (
    <div className="animate-fadeIn space-y-8">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-4 mb-6">
          <h1 className="text-4xl font-bold text-gray-900">{word.japanese}</h1>
          {word.audioUrl && (
            <Button
              variant="outline"
              size="icon"
              onClick={() => playAudio(word.audioUrl)}
            >
              <Volume2 className="h-6 w-6" />
            </Button>
          )}
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
              <CardTitle>Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between text-lg">
                <span>Correct: <span className="text-green-600">{word.correct}</span></span>
                <span>Wrong: <span className="text-red-600">{word.wrong}</span></span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Example Usage</h2>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {word.examples.map((example, index) => (
            <div key={index} className="p-4 border-b last:border-b-0">
              <p className="text-lg mb-2">{example.japanese}</p>
              <p className="text-gray-600 mb-1">{example.romaji}</p>
              <p className="text-gray-500">{example.english}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WordShow;

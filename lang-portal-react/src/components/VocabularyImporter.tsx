import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import { api } from '@/services/api';

export function VocabularyImporter() {
    const [theme, setTheme] = useState('');
    const [generatedVocab, setGeneratedVocab] = useState('');
    const [rawResponse, setRawResponse] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();

    const generateVocabulary = async () => {
        try {
            setIsLoading(true);
            const data = await api.generateVocabulary(theme);
            setGeneratedVocab(JSON.stringify(data, null, 2));
        } catch (error: any) {
            setGeneratedVocab(error.message);
            toast({
                title: "Error",
                description: error.message,
                variant: "destructive"
            });
        } finally {
            setIsLoading(false);
        }
    };

    const copyToClipboard = async () => {
        await navigator.clipboard.writeText(generatedVocab);
        toast({
            title: "Success",
            description: "Copied to clipboard!",
        });
    };

    return (
        <div className="space-y-4 p-4">
            <div className="space-y-2">
                <label className="text-sm font-medium">Theme</label>
                <Input
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                    placeholder="Enter vocabulary theme (e.g., 'Greetings', 'Food')"
                />
            </div>

            <Button 
                onClick={generateVocabulary}
                disabled={isLoading || !theme}
            >
                {isLoading ? 'Generating...' : 'Generate Vocabulary'}
            </Button>

            {rawResponse && (
                <div className="space-y-2">
                    <div className="flex justify-between">
                        <label className="text-sm font-medium">Raw Response</label>
                    </div>
                    <Textarea
                        value={rawResponse}
                        readOnly
                        className="font-mono h-[300px] bg-gray-50"
                    />
                </div>
            )}

            {generatedVocab && (
                <div className="space-y-2">
                    <div className="flex justify-between">
                        <label className="text-sm font-medium">Generated Vocabulary</label>
                        <Button 
                            variant="outline" 
                            size="sm"
                            onClick={copyToClipboard}
                        >
                            Copy
                        </Button>
                    </div>
                    <Textarea
                        value={generatedVocab}
                        readOnly
                        className="font-mono h-[300px]"
                    />
                </div>
            )}
        </div>
    );
}

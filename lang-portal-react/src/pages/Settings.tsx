import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { useTheme } from "@/contexts/ThemeContext";

const Settings = () => {
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();

  const [isDarkModeChecked, setIsDarkModeChecked] = useState(theme === 'dark');

  useEffect(() => {
    setIsDarkModeChecked(theme === 'dark');
  }, [theme]);

  const handleReset = () => {
    if (confirmText.toLowerCase() === "reset me") {
      // TODO: Implement actual reset functionality
      toast({
        title: "Reset Complete",
        description: "Your history has been reset successfully.",
      });
      setIsConfirmOpen(false);
    } else {
      toast({
        title: "Invalid Confirmation",
        description: "Please type 'reset me' to confirm.",
        variant: "destructive",
      });
    }
  };

  const handleDarkModeToggle = (checked: boolean) => {
    const newTheme = checked ? 'dark' : 'light';
    setTheme(newTheme);
    setIsDarkModeChecked(checked);
  };

  return (
    <div className="animate-fadeIn">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>
      
      <div className="space-y-8">
        <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Dark Mode</h3>
            <p className="text-sm text-gray-500">Toggle dark mode on or off</p>
          </div>
          <Switch
            checked={isDarkModeChecked}
            onCheckedChange={handleDarkModeToggle}
            aria-label="Toggle dark mode"
          />
        </div>

        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Reset History</h3>
          <p className="text-sm text-gray-500 mb-4">
            This will permanently delete all your study history and progress.
          </p>
          <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
            <DialogTrigger asChild>
              <Button variant="destructive">Reset History</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Are you sure?</DialogTitle>
                <DialogDescription>
                  This action cannot be undone. Type "reset me" to confirm.
                </DialogDescription>
              </DialogHeader>
              <Input
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="Type 'reset me' to confirm"
              />
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setIsConfirmOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleReset}
                  disabled={confirmText.toLowerCase() !== "reset me"}
                >
                  Reset
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </div>
  );
};

export default Settings;

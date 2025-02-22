import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";

import Navigation from "@/components/Navigation";
import Breadcrumbs from "@/components/Breadcrumbs";
import Dashboard from "@/pages/Dashboard";
import StudyActivities from "@/pages/StudyActivities";
import StudyActivityShow from "@/pages/StudyActivityShow";
import Words from "@/pages/Words";
import WordShow from "@/pages/WordShow";
import Groups from "@/pages/Groups";
import GroupShow from "@/pages/GroupShow";
import Sessions from "@/pages/Sessions";
import Settings from "@/pages/Settings";
import { VocabularyImporter } from '@/components/VocabularyImporter';

const queryClient = new QueryClient();

const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen bg-gray-50">
    <Navigation />
    <main className="pt-20 pb-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <Breadcrumbs />
      {children}
    </main>
  </div>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/study_activities" element={<StudyActivities />} />
            <Route path="/study_activities/:id" element={<StudyActivityShow />} />
            <Route path="/words" element={<Words />} />
            <Route path="/words/:id" element={<WordShow />} />
            <Route path="/groups" element={<Groups />} />
            <Route path="/groups/:id" element={<GroupShow />} />
            <Route path="/sessions" element={<Sessions />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/vocabulary-importer" element={<VocabularyImporter />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

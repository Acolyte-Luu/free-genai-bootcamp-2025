import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { BookOpen } from "lucide-react";

const NavItem = ({ href, children }: { href: string; children: React.ReactNode }) => {
  const location = useLocation();
  const isActive = location.pathname === href;

  return (
    <Link
      to={href}
      className={cn(
        "px-4 py-2 rounded-lg transition-all duration-200",
        "hover:bg-japanese-100 hover:text-japanese-700",
        "focus:outline-none focus:ring-2 focus:ring-japanese-200",
        isActive
          ? "bg-japanese-50 text-japanese-600 font-medium"
          : "text-gray-600"
      )}
    >
      {children}
    </Link>
  );
};

const Navigation = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-sm border-b border-gray-100 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex-shrink-0">
            <Link to="/dashboard" className="text-japanese-600 font-bold text-xl">
              日本語
            </Link>
          </div>
          <div className="hidden sm:block">
            <div className="flex items-center space-x-4">
              <NavItem href="/dashboard">Dashboard</NavItem>
              <NavItem href="/study_activities">Study Activities</NavItem>
              <NavItem href="/words">Words</NavItem>
              <NavItem href="/groups">Word Groups</NavItem>
              <NavItem href="/settings">Settings</NavItem>
              <NavItem href="/vocabulary-importer">
                <BookOpen className="w-4 h-4 mr-2" />
                Vocabulary Importer
              </NavItem>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;

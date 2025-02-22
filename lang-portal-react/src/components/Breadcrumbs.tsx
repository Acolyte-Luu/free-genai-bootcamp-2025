
import { Link, useLocation } from "react-router-dom";
import { ChevronRight } from "lucide-react";

const getBreadcrumbText = (path: string) => {
  const parts = path.split("/").filter(Boolean);
  const last = parts[parts.length - 1];
  return last
    .split("_")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const Breadcrumbs = () => {
  const location = useLocation();
  const pathSegments = location.pathname.split("/").filter(Boolean);

  return (
    <nav aria-label="Breadcrumb" className="mb-6">
      <ol className="flex items-center space-x-2">
        <li>
          <Link
            to="/dashboard"
            className="text-gray-500 hover:text-japanese-600 transition-colors"
          >
            Dashboard
          </Link>
        </li>
        {pathSegments.map((segment, index) => (
          <li key={segment} className="flex items-center space-x-2">
            <ChevronRight className="w-4 h-4 text-gray-400" />
            <Link
              to={`/${pathSegments.slice(0, index + 1).join("/")}`}
              className={`${
                index === pathSegments.length - 1
                  ? "text-japanese-600 font-medium"
                  : "text-gray-500 hover:text-japanese-600"
              } transition-colors`}
            >
              {getBreadcrumbText(segment)}
            </Link>
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;

import {
  IconBriefcase,
  IconDashboard,
  IconSettings,
  IconUserCircle,
} from "@tabler/icons-react";
import type { NavItem } from "@/types/nav-item";

export const navLinks: NavItem[] = [
  { label: "Dashboard", icon: IconDashboard, link: "/dashboard" },
  {
    label: "Applications",
    icon: IconBriefcase,
    initiallyOpened: true,
    links: [
      { label: "All applications", link: "/applications" },
      { label: "Add application", link: "/applications/new" },
    ],
  },
  {
    label: "Admin",
    icon: IconSettings,
    initiallyOpened: false,
    links: [
      { label: "Settings", link: "/admin/settings" },
      { label: "Users", link: "/admin/users" },
    ],
  },
];

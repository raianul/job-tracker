"use client";

import { Menu, UnstyledButton } from "@mantine/core";
import { ScrollArea } from "@mantine/core";
import { IconLogout } from "@tabler/icons-react";
import { UserButton } from "@/components/UserButton/UserButton";
import type { NavItem } from "@/types/nav-item";
import { NavLinksGroup } from "./NavLinksGroup";
import { useAuth } from "@/contexts/AuthContext";
import classes from "./Navbar.module.css";

interface Props {
  data: NavItem[];
  hidden?: boolean;
}

export function Navbar({ data }: Props) {
  const { user, logout } = useAuth();
  const filteredData = user?.is_admin ? data : data.filter((item) => item.label !== "Admin");
  const links = filteredData.map((item) => (
    <NavLinksGroup key={item.label} {...item} />
  ));

  return (
    <>
      <ScrollArea className={classes.links}>
        <div className={classes.linksInner}>{links}</div>
      </ScrollArea>

      <div className={classes.footer}>
        <Menu shadow="md" width={220} position="right-end">
          <Menu.Target>
            <UnstyledButton style={{ width: "100%" }}>
              <UserButton
                image={user?.avatar_url || ""}
                name={user?.name || user?.email || "User"}
                email={user?.email || ""}
              />
            </UnstyledButton>
          </Menu.Target>
          <Menu.Dropdown>
            <Menu.Item leftSection={<IconLogout size={14} />} onClick={logout}>
              Logout
            </Menu.Item>
          </Menu.Dropdown>
        </Menu>
      </div>
    </>
  );
}

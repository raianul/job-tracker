import { Text } from "@mantine/core";
import Link from "next/link";
import classes from "./Logo.module.css";

export const Logo: React.FC = () => {
  return (
    <Link href="/" className={classes.heading}>
      <Text fw="bolder" size="xl">
        Job Tracker Panel
      </Text>
    </Link>
  );
};

import { Text, View } from "react-native";
import { Link } from "expo-router";
import { Button } from "react-native-paper";

export default function NotificationsScreen() {
  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Text>This is the notifications screen</Text>
      <Link href="/HomeScreen" asChild>
        <Button mode="contained">
            Home
        </Button>
      </Link>
    </View>
  );
}

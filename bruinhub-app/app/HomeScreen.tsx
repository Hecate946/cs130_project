import AsyncStorage from "@react-native-async-storage/async-storage";
import { Link } from "expo-router";
import { Text, View } from "react-native";
import { Button } from "react-native-paper";
import { useColorScheme } from "@/hooks/useColorScheme";

interface HomeScreenProps {
  onFinish: () => void;
};

export default function HomeScreen({ onFinish }: HomeScreenProps) {
  const colorScheme = useColorScheme();

  // TODO: REMOVE this function and onFinish prop
  // FOR TESTING/DEV PURPOSES -- RETURN TO ONBOARDING SCREEN
  const handleFinish = async () => {
    await AsyncStorage.setItem("finishedOnboarding", "false");
    onFinish();
  };


  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Text>This is the home screen</Text>
      <Link href="/" asChild>
        <Button mode="contained" onPress={handleFinish}>
            Back to onboarding for dev purposes
        </Button>
      </Link>
      <Link href="/NotificationsScreen" asChild>
        <Button mode="contained">
            To Notifs
        </Button>
      </Link>
    </View>
  );
}

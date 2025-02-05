import { Stack } from "expo-router";
import { PaperProvider } from "react-native-paper";

export default function RootLayout() {

  return (
    <PaperProvider>
      <Stack>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="NotificationsScreen" options={{ headerShown: false }} />
        <Stack.Screen name="OnboardingScreen" options={{ headerShown: false }} />
      </Stack>
    </PaperProvider>
  );
}

// components/recreation/ReservationScreen.tsx
import React, { useEffect, useState } from 'react';
import { View, Modal } from 'react-native';
import LoginWebView from './LoginWebView';
import ReservationInterface from './ReservationInterface'; // And this one

const ReservationScreen: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [showLogin, setShowLogin] = useState<boolean>(false);

  useEffect(() => {
    // TODO: Call your backend endpoint to check authentication status.
    // For now, simulate a not-authenticated state.
    setShowLogin(true);
  }, []);

  const handleLoginSuccess = (): void => {
    setShowLogin(false);
    setIsAuthenticated(true);
  };

  return (
    <View style={{ flex: 1 }}>
      {showLogin && (
        <Modal visible={showLogin} animationType="slide">
          <LoginWebView onLoginSuccess={handleLoginSuccess} />
        </Modal>
      )}
      {isAuthenticated && <ReservationInterface />}
    </View>
  );
};

export default ReservationScreen;

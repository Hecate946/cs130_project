// components/recreation/LoginWebView.tsx
import React from 'react';
import { WebView, WebViewNavigation } from 'react-native-webview';
import CookieManager from '@react-native-cookies/cookies';

interface LoginWebViewProps {
  onLoginSuccess: () => void;
}

const LOGIN_URL = 'https://secure.recreation.ucla.edu/account/login';

const LoginWebView: React.FC<LoginWebViewProps> = ({ onLoginSuccess }) => {
  const handleNavigationStateChange = (navState: WebViewNavigation) => {
    // Use a condition that identifies a successful login page.
    // For example, if the URL contains 'dashboard' or 'profile' after login.
    // Retrieve cookies for the domain.
    CookieManager.get('https://secure.recreation.ucla.edu/')
    .then((cookies) => {
        console.log('Cookies retrieved:', cookies);
        const aspCookie = cookies['.AspNet.ApplicationCookie'];
        if (aspCookie) {
        console.log('AspNet Application Cookie found:', aspCookie.value);
        onLoginSuccess();
        } else {
        console.log('AspNet Application Cookie not found yet.');
        }
    })
    .catch((error) => {
        console.error('Error retrieving cookies:', error);
    });
  };

  return (
    <WebView
      source={{ uri: LOGIN_URL }}
      onNavigationStateChange={handleNavigationStateChange}
    />
  );
};

export default LoginWebView;


import "./globals.css";
import { RepositoryProvider } from "./context/RepositoryContext";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
    >
      <body>
        <RepositoryProvider>
        {children}
        </RepositoryProvider>
        
        </body>
    </html>
  );
}

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Orbix Network Admin',
  description: 'Admin dashboard for Orbix Network',
}

export const dynamic = 'force-dynamic'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" style={{ colorScheme: 'light' }}>
      <head>
        <meta name="color-scheme" content="light" />
        <meta name="theme-color" content="#ffffff" />
        <style dangerouslySetInnerHTML={{__html: `
          * {
            color-scheme: light !important;
          }
          input[type="email"],
          input[type="password"],
          input[type="text"],
          input[type="number"],
          textarea,
          select {
            color: #111827 !important;
            background-color: #ffffff !important;
            -webkit-text-fill-color: #111827 !important;
          }
          input[type="email"]::placeholder,
          input[type="password"]::placeholder,
          input[type="text"]::placeholder {
            color: #9ca3af !important;
            -webkit-text-fill-color: #9ca3af !important;
          }
        `}} />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}


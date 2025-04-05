import { PropsWithChildren } from "react"
import { ModeToggle } from "./mode-toggle"

export function GameLayout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="w-full flex items-center justify-between py-4 px-4">
          <h1 className="text-2xl font-bold">Japanese MUD Adventure</h1>
          <ModeToggle />
        </div>
      </header>
      <main className="w-full py-4">
        {children}
      </main>
      <footer className="border-t py-4">
        <div className="w-full px-4 text-center text-sm text-muted-foreground">
          JP-MUD - Japanese Learning Adventure © {new Date().getFullYear()}
        </div>
      </footer>
    </div>
  )
} 
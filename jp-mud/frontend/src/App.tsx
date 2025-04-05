import GameContainer from './components/GameContainer';
import { GameLayout } from './components/game-layout';
import { ThemeProvider } from './components/theme-provider';

function App() {
  return (
    <ThemeProvider>
      <GameLayout>
        <GameContainer />
      </GameLayout>
    </ThemeProvider>
  );
}

export default App;

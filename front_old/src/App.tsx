import { Outlet, Link } from "react-router-dom";


// const handleTouchMove = (e: { preventDefault: () => void; }) => {
//   e.preventDefault();
// };
// document.body.addEventListener('touchmove', handleTouchMove, { passive: false });



function App() {
  return <Outlet />
}

export default App;

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Console from './console/console';
import ShowCommandPanel from './show_command_panel/show_command_pannel';
import { Viewer } from './viewer/viewer';


const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />}>
        <Route path="" element={<Console />} />
        <Route path="/show" element={<ShowCommandPanel />} />
        <Route path="/view" element={<Viewer />} />
        {/* <Route path="learn" element={<Learn />} />
        <Route path="contribute" element={<Contribute />} />
        <Route path="view" element={<View />} />
        <Route path="edit" element={<Edit />} />
        <Route path="signout" element={<SignOut />} />
        <Route path="admin" element={<AdminHome />} /> */}
      </Route>
    </Routes>
  </BrowserRouter>
);


// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();



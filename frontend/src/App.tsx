import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import FacultyManagement from './pages/FacultyManagement'
import ClassManagement from './pages/ClassManagement'
import SubjectManagement from './pages/SubjectManagement'
import GenerateTimetable from './pages/GenerateTimetable'
import ViewTimetable from './pages/ViewTimetable'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/faculty" element={<FacultyManagement />} />
        <Route path="/classes" element={<ClassManagement />} />
        <Route path="/subjects" element={<SubjectManagement />} />
        <Route path="/generate" element={<GenerateTimetable />} />
        <Route path="/timetable/:classId" element={<ViewTimetable />} />
      </Routes>
    </Layout>
  )
}

export default App

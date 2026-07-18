import About from './components/About';
import ContactForm from './components/ContactForm';
import Footer from './components/Footer';
import Header from './components/Header';
import Hero from './components/Hero';
import Skills from './components/Skills';

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      <Header />
      <main>
        <Hero />
        <About />
        <Skills />
        <ContactForm />
      </main>
      <Footer />
    </div>
  );
}

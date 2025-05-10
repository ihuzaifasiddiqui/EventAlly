import HeroSection from './HeroSection';
import Features from './features'; // Adjust the path to where your Features component is located

const Home = () => {
  return (
    <div className='flex flex-col align-center items-center w-full h-full overflow-y-auto'>
     <HeroSection/>
     <Features/>
    </div>
  );
};

export default Home;
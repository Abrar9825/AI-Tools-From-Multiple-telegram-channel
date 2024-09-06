import React, { useEffect, useState } from 'react';
import axios from 'axios';

const MediaDisplay = () => {
  const [mediaData, setMediaData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api');
        setMediaData(response.data.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {mediaData.map((message, index) => (
        <div key={index}>
          <h3>Channel: {message.channel}</h3>
          <p>Message ID: {message.id}</p>
          <p>Text: {message.text}</p>
          <p>Labels :{message.label}</p>
          {message.photo_path && (
            <div>
              <h4>Photo:</h4>
              <img src={`http://localhost:8000/downloads/${message.channel}/${message.photo_path}`} alt="Photo" style={{ width: '300px' }} />
            </div>
          )}
          {message.video_path && (
            <div>
              <h4>Video:</h4>
              <video controls style={{ width: '300px' }}>
                <source src={`http://localhost:8000/downloads/${message.channel}/${message.video_path}`} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default MediaDisplay;

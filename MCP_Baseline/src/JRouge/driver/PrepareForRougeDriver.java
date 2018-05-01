package JRouge.driver;

import java.io.File;

import JRouge.rouge.serializer.RougeSeeFormatSerializer;

public class PrepareForRougeDriver
{
    public static void main(String[] args)
    {
	RougeSeeFormatSerializer s = new RougeSeeFormatSerializer();
	s.serialize(s.prepareForRouge(new File("C:\\Users\\Marina\\Desktop\\muse_test_data\\English\\Documents"), 
		                      new File("C:\\Users\\Marina\\Desktop\\muse_test_data\\English\\Gold Standard")), 
		    new File("output"));
    }
    
}

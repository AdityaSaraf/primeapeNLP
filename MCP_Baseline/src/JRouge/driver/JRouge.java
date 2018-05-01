package JRouge.driver;

import JRouge.interfaces.IRouge;
import JRouge.interfaces.IRougeSummaryModel;

import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import org.apache.commons.math3.distribution.NormalDistribution;
import org.apache.commons.math3.stat.descriptive.SummaryStatistics;

import JRouge.rouge.RougeN;
import JRouge.rouge.serializer.RougeSeeFormatSerializer;

import com.martiansoftware.jsap.FlaggedOption;
import com.martiansoftware.jsap.JSAP;
import com.martiansoftware.jsap.JSAPException;
import com.martiansoftware.jsap.JSAPResult;
import com.martiansoftware.jsap.QualifiedSwitch;
import com.martiansoftware.jsap.Switch;
import com.martiansoftware.jsap.stringparsers.FileStringParser;

import JRouge.common.ScoreType;

public class JRouge
{
    public enum Config
    {
	DOCUMENT_PATH("peersPath"),
	GOLD_STANDARD_PATH("goldStandardPath"),
	WORD_LIMIT("wordLimit"),
	BYTE_LIMIT("byteLimit"),
	GRAM_SIZE("ngramSize"),
	METHOD("method"),
	ALPHA("alpha"),
	CONFIDENCE("confidence"),
	VERBOSE("verbose");

	private String value;

	private Config(String value)
	{
	    this.value = value;
	}

	@Override
	public String toString()
	{
	    return value;
	}
    }

    public static void main(String[] args) throws JSAPException
    {
	JSAP jsap = initArgsParser();
	JSAPResult parsedArgs = jsap.parse(args);
	checkIfArgsParsedSuccessfully(jsap, parsedArgs);
	RougeSeeFormatSerializer s = new RougeSeeFormatSerializer();
	Map<IRougeSummaryModel, Set<IRougeSummaryModel>> results = s.prepareForRouge(parsedArgs.getFile(Config.DOCUMENT_PATH.toString()), parsedArgs.getFile(Config.GOLD_STANDARD_PATH.toString()));

	SummaryStatistics rss = new SummaryStatistics();
	SummaryStatistics pss = new SummaryStatistics();
	SummaryStatistics fss = new SummaryStatistics();

	System.out.println("ROUGE-" + parsedArgs.getInt(Config.GRAM_SIZE.toString()));
	IRouge rouge = null;
	RougeN.DEBUG = parsedArgs.getBoolean(Config.VERBOSE.toString());
	for (IRougeSummaryModel document : results.keySet())
	{
	    rouge = new RougeN(
		    document,
		    results.get(document),
		    parsedArgs.getInt(Config.BYTE_LIMIT.toString()),
		    parsedArgs.getInt(Config.WORD_LIMIT.toString()),
		    parsedArgs.getInt(Config.GRAM_SIZE.toString()),
		    parsedArgs.getChar(Config.METHOD.toString()),
		    parsedArgs.getDouble(Config.ALPHA.toString())
		    );

	    Map<ScoreType, Double> scores = rouge.evaluate();

	    rss.addValue(scores.get(ScoreType.R));
	    pss.addValue(scores.get(ScoreType.P));
	    fss.addValue(scores.get(ScoreType.F));
	}

	boolean calculateConfidenceInterval = parsedArgs.getBoolean(Config.CONFIDENCE.toString());
	double confidence = 0;
	if (calculateConfidenceInterval)
	{
	    confidence = parsedArgs.getDouble(Config.CONFIDENCE.toString());
	}

	System.out.println("Average_R: " + rss.getMean() + (calculateConfidenceInterval ? " " + getConfidenceInterval(rss, confidence) : ""));
	System.out.println("Average_P: " + pss.getMean() + (calculateConfidenceInterval ? " " + getConfidenceInterval(pss, confidence) : ""));
	System.out.println("Average_F: " + fss.getMean() + (calculateConfidenceInterval ? " " + getConfidenceInterval(fss, confidence) : ""));
    }

    private static String getConfidenceInterval(SummaryStatistics statistics, double confidence)
    {
	StringBuilder sb = new StringBuilder("Confidence interval (" + confidence * 100 + "%): ");

	//it is possible to change to T-distribution and provide statistics.getN()-1 freedom degree
	double sampleError = new NormalDistribution(0, 1).inverseCumulativeProbability(confidence) * (statistics.getStandardDeviation() / Math.sqrt(statistics.getN()));
	sb.append("(" + (statistics.getMean() - sampleError) + " <= " + statistics.getMean() + " <= " + (statistics.getMean() + sampleError) + ")");

	return sb.toString();
    }

    private static void checkIfArgsParsedSuccessfully(JSAP jsap, JSAPResult results)
    {
	if (!results.success())
	{
	    System.err.println();

	    for (@SuppressWarnings("rawtypes")
	    Iterator errs = results.getErrorMessageIterator(); errs.hasNext();)
	    {
		System.err.println("Error: " + errs.next());
	    }

	    System.err.println();
//	    System.err.println("Usage: java " + JRougeN_Driver.class.getSimpleName());
	    System.err.println("                " + jsap.getUsage());
	    System.err.println();
	    System.err.println(jsap.getHelp());
	    System.exit(1);
	}
    }

    private static JSAP initArgsParser() throws JSAPException
    {
	JSAP jsap = new JSAP();

	FlaggedOption opt1 = new FlaggedOption(Config.DOCUMENT_PATH.toString()).setStringParser(FileStringParser.getParser())
									       .setRequired(true)
									       .setShortFlag('p')
									       .setLongFlag("peer");

	opt1.setHelp("The path to the peer summaries.");
	jsap.registerParameter(opt1);

	FlaggedOption opt2 = new FlaggedOption(Config.GOLD_STANDARD_PATH.toString()).setStringParser(FileStringParser.getParser())
										    .setRequired(true)
										    .setShortFlag('g')
										    .setLongFlag("goldstandard");

	opt2.setHelp("The path to the gold standard summaries.");
	jsap.registerParameter(opt2);

	FlaggedOption opt3 = new FlaggedOption(Config.GRAM_SIZE.toString()).setStringParser(JSAP.INTEGER_PARSER)
									   .setRequired(true)
									   .setShortFlag('n')
									   .setLongFlag(JSAP.NO_LONGFLAG);

	opt3.setHelp("The size of the gram to use.");
	jsap.registerParameter(opt3);

	FlaggedOption opt4 = new FlaggedOption(Config.WORD_LIMIT.toString()).setStringParser(JSAP.INTEGER_PARSER)
									    .setRequired(false)
									    .setDefault(Integer.MAX_VALUE + "")
									    .setShortFlag('l')
									    .setLongFlag(JSAP.NO_LONGFLAG);

	opt4.setHelp("The number of words to use from the texts.");
	jsap.registerParameter(opt4);

	FlaggedOption opt5 = new FlaggedOption(Config.BYTE_LIMIT.toString()).setStringParser(JSAP.INTEGER_PARSER)
									    .setRequired(false)
									    .setDefault(Integer.MAX_VALUE + "")
									    .setShortFlag('b')
									    .setLongFlag(JSAP.NO_LONGFLAG);

	opt5.setHelp("The number of bytes to use from each text.");
	jsap.registerParameter(opt5);

	FlaggedOption opt6 = new FlaggedOption(Config.ALPHA.toString()).setStringParser(JSAP.DOUBLE_PARSER)
								       .setRequired(false)
								       .setDefault("0.5")
								       .setShortFlag('a')
								       .setLongFlag(JSAP.NO_LONGFLAG);

	opt6.setHelp("The alpha value used to calculate F metric");
	jsap.registerParameter(opt6);

	FlaggedOption opt7 = new FlaggedOption(Config.METHOD.toString()).setStringParser(JSAP.CHARACTER_PARSER)
									.setRequired(false)
									.setDefault("A")
									.setShortFlag('m')
									.setLongFlag(JSAP.NO_LONGFLAG);

	opt7.setHelp("The method used to calculate the metrics. Use 'A' for average, use 'B' for best.");
	jsap.registerParameter(opt7);

	Switch opt8 = new Switch(Config.VERBOSE.toString()).setDefault("false")
							  .setShortFlag('v')
							  .setLongFlag(JSAP.NO_LONGFLAG);

	opt8.setHelp("Show verbose data during run.");
	jsap.registerParameter(opt8);

	QualifiedSwitch opt9 = (QualifiedSwitch) new QualifiedSwitch(Config.CONFIDENCE.toString()).setShortFlag('c')
												  .setLongFlag("confidence")
												  .setList(JSAP.NOT_LIST)
												  .setStringParser(JSAP.DOUBLE_PARSER)
												  .setRequired(false);
	opt9.setHelp("Calculate and show confidence intervals");
	jsap.registerParameter(opt9);

	return jsap;
    }
}

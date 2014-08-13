package edu.uw.nlp.treckba.plot

import org.apache.commons.cli._
import org.apache.commons.lang.Validate
import org.sameersingh.scalaplot.Style
import org.sameersingh.scalaplot.gnuplot.GnuplotPlotter
import org.sameersingh.scalaplot.metrics.PrecRecallCurve

import scala.collection.mutable.ArrayBuffer
import scala.io.Source

object PrecisionRecall {

  def main(args: Array[String]) {

    val options = new Options()
    options.addOption("i", true, "input files")
    options.addOption("o", true, "output directory")
    options.addOption("f", true, "output filename")

    val parser = new BasicParser()

    var inputFiles: Array[String] = null
    var outputDir: String = null
    var outFilename: String = null
    try {
      val line = parser.parse(options, args)
      inputFiles = line.getOptionValue("i").split(",")
      Validate.notNull(inputFiles)
      outputDir = line.getOptionValue("o")
      Validate.notNull(outputDir)
      outFilename = line.getOptionValue("f")
      Validate.notNull(outFilename)

    } catch {
      case ex: Exception => {
        val formatter = new HelpFormatter()
        formatter.printHelp("precisionrecall", options)
        return
      }
    }

    val lists : ArrayBuffer[ArrayBuffer[(Double, Boolean)]] = new ArrayBuffer[ArrayBuffer[(Double, Boolean)]]
    for (file <- inputFiles) {
      val list = new ArrayBuffer[(Double, Boolean)]
      for (line <- Source.fromFile(file).getLines) {
        val values = line.split(" ")
        val prob = values(0).toDouble
        var truth = false
        if (values(1).toInt == 1)
          truth = true
        val tuple = (prob, truth)
        list += tuple
      }
      lists += list
    }

    val length = lists.length
    val curve = new PrecRecallCurve(lists(0))
    val chart = curve.prChart("Precision Recall")

    for (index <- 1 to length-1) {
      val anotherCurve = new PrecRecallCurve(lists(index))
      val anotherChart = anotherCurve.prChart("Precision Recall")
      chart.data += anotherChart.data.serieses.head
    }
    chart.data.serieses.foreach(_.pointType= Some(Style.PointType.Dot))
    val plotter = new GnuplotPlotter(chart)
    plotter.png(outputDir, outFilename)
  }
}

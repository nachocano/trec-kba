package edu.uw.nlp.treckba.plot

import org.apache.commons.cli._
import org.apache.commons.lang.Validate
import org.sameersingh.scalaplot.Style
import org.sameersingh.scalaplot.gnuplot.GnuplotPlotter
import org.sameersingh.scalaplot.metrics.PrecRecallCurve

import scala.collection.mutable.ArrayBuffer
import scala.io.Source

object Threshold {

  def main(args: Array[String]) {
    val options = new Options()
    options.addOption("i", true, "input file")
    options.addOption("o", true, "output directory")
    options.addOption("f", true, "output filename")

    val parser = new BasicParser()

    var inputFile: String = null
    var outputDir: String = null
    var outFilename: String = null
    try {
      val line = parser.parse(options, args)
      inputFile = line.getOptionValue("i")
      Validate.notNull(inputFile)
      outputDir = line.getOptionValue("o")
      Validate.notNull(outputDir)
      outFilename = line.getOptionValue("f")
      Validate.notNull(outFilename)

    } catch {
      case ex: Exception => {
        val formatter = new HelpFormatter()
        formatter.printHelp("threshold", options)
        return
      }
    }

    val list = new ArrayBuffer[(Double, Boolean)]
    for (line <- Source.fromFile(inputFile).getLines) {
      val values = line.split(" ")
      val prob = values(0).toDouble
      var truth = false
      if (values(1).toInt == 1)
        truth = true
      val tuple = (prob, truth)
      list += tuple
    }

    val curve = new PrecRecallCurve(list)
    val threshold = curve.prThreshChart("Threshold")
    threshold.showLegend = true
    threshold.data.serieses.foreach(_.pointType= Some(Style.PointType.Dot))
    val plotter = new GnuplotPlotter(threshold)
    plotter.png(outputDir, outFilename + "-thresh")


  }
}

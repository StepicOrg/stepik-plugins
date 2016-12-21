import scala.io.Source

object Main {
  def main(args: Array[String]) {
    val secretSource = Source.fromFile("{{ SECRET_FILE }}")
    println(secretSource.getLines.next())
    secretSource.close
  }
}

"""End-to-end tests involing scanning and parsing."""
from nast import parsing
from nast import scanner


def test_simple():
    """Test a single parameter model."""
    code = """
        parameters {
          real a;
        }
        """
    lexer = scanner.Scanner(code)
    tokens = lexer.scan_tokens()

    parser = parsing.Parser(tokens)

    result = parser.parse()

    print(result)


def test_simple_normal():
    """Test a simple model sampling from a normal distribution."""
    code = """
        parameters {
          real a;   // a variable
        }
        model {
            a ~ normal(0, 1);   // standard normal
        }
        """
    lexer = scanner.Scanner(code)
    tokens = lexer.scan_tokens()

    parser = parsing.Parser(tokens)

    result = parser.parse()

    print(result)


def test_eight_schools():
    """Test infamous 8 schools model."""
    code = """
        data {
          int<lower=0> J;         // number of schools
          real y[J];              // estimated treatment effects
          real<lower=0> sigma[J]; // standard error of effect estimates
        }
        parameters {
          real mu;                // population treatment effect
          real<lower=0> tau;      // standard deviation in treatment effects
          vector[J] eta;          // unscaled deviation from mu by school
        }
        transformed parameters {
          vector[J] theta = mu + tau * eta;        // school treatment effects
        }
        model {
          target += normal_lpdf(eta | 0, 1);       // prior log-density
          target += normal_lpdf(y | theta, sigma); // log-likelihood
        }
        """
    lexer = scanner.Scanner(code)
    tokens = lexer.scan_tokens()

    parser = parsing.Parser(tokens)

    result = parser.parse()

    print(result)


def test_all_blocks():
    """Test program with all blocks."""
    code = """
    functions {
      real relative_diff(real x, real y) {
        real abs_diff;
        real avg_scale;
        abs_diff = fabs(x - y);
        avg_scale = (fabs(x) + fabs(y)) / 2;
        return abs_diff / avg_scale;
      }
    }
    data {
        int M;
        real x[M];
    }
    tranformed data {
        int M_squared;
        int x_squared;

        M_squared = M^2;
        x_squared = x.^2;
    }
    parameters {
        real a;
        real b;
    }
    transformed parameters {
        real ab = a * b;
    }
    model {
        a ~ normal(0, 2);
        b ~ normal(2, 2);
    }
    generated quantities {
      real rdiff;
      rdiff = relative_diff(alpha, beta);
    }
    """
